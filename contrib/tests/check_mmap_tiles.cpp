// Validate generated movement tiles with the same Detour library as the server.
// This checks loadability; it does not prove that a route is correct ingame.
#include "MapDefines.h"
#include "DetourAlloc.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <stdexcept>
#include <vector>

namespace fs = std::filesystem;

struct NavMeshDeleter
{
    void operator()(dtNavMesh* mesh) const { dtFreeNavMesh(mesh); }
};

int main(int argc, char** argv)
{
    if (argc != 2)
    {
        std::cerr << "Usage: check_mmap_tiles <mmaps-directory>\n";
        return 2;
    }

    std::size_t checked = 0;
    std::size_t failures = 0;
    std::map<std::string, std::unique_ptr<dtNavMesh, NavMeshDeleter>> meshes;
    try
    {
        std::vector<fs::path> tiles;
        for (auto const& entry : fs::directory_iterator(argv[1]))
        {
            auto const path = entry.path();
            if (path.extension() == ".mmtile")
                tiles.push_back(path);
            else if (path.extension() == ".mmap")
            {
                std::ifstream input(path, std::ios::binary);
                dtNavMeshParams params{};
                if (fs::file_size(path) != sizeof(params) ||
                    !input.read(reinterpret_cast<char*>(&params), sizeof(params)))
                    throw std::runtime_error("Invalid map parameters: " + path.filename().string());
                std::unique_ptr<dtNavMesh, NavMeshDeleter> mesh(dtAllocNavMesh());
                // The 64-bit Detour build uses fixed polygon bits; its stored
                // maxPolys value may have bit 31 set in the signed field.
                if (!mesh || params.maxTiles <= 0 ||
                    dtStatusFailed(mesh->init(&params)))
                    throw std::runtime_error("Detour rejected map parameters: " + path.filename().string());
                meshes.emplace(path.stem().string(), std::move(mesh));
            }
        }

        std::sort(tiles.begin(), tiles.end());
        for (auto const& path : tiles)
        {
            ++checked;
            try
            {
                std::ifstream input(path, std::ios::binary);
                MmapTileHeader header;
                if (!input.read(reinterpret_cast<char*>(&header), sizeof(header)) ||
                    header.mmapMagic != MMAP_MAGIC || header.mmapVersion != MMAP_VERSION ||
                    header.dtVersion != DT_NAVMESH_VERSION || header.size < sizeof(dtMeshHeader) ||
                    header.size > std::numeric_limits<int>::max() ||
                    fs::file_size(path) != sizeof(header) + header.size)
                    throw std::runtime_error("Invalid header or truncated payload");

                auto const name = path.stem().string();
                auto const separator = name.find('_');
                auto const found = meshes.find(name.substr(0, separator));
                if (separator == std::string::npos || found == meshes.end())
                    throw std::runtime_error("Missing map parameters");

                std::vector<unsigned char> payload(header.size);
                if (!input.read(reinterpret_cast<char*>(payload.data()), payload.size()))
                    throw std::runtime_error("Could not read tile payload");
                dtTileRef reference = 0;
                auto* mesh = found->second.get();
                if (dtStatusFailed(mesh->addTile(payload.data(), int(payload.size()), 0, 0, &reference)))
                    throw std::runtime_error("Detour rejected tile payload");
                if (dtStatusFailed(mesh->removeTile(reference, nullptr, nullptr)))
                    throw std::runtime_error("Detour could not unload tile");
            }
            catch (std::exception const& error)
            {
                ++failures;
                std::cerr << path.filename().string() << ": " << error.what() << '\n';
            }
        }
        if (checked == 0)
            throw std::runtime_error("No movement tiles found");
    }
    catch (std::exception const& error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }

    std::cout << "{\"maps\":" << meshes.size() << ",\"tiles\":" << checked
              << ",\"failures\":" << failures << "}\n";
    return failures ? 1 : 0;
}
