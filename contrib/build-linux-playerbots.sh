#!/usr/bin/env bash
set -euo pipefail

# Ubuntu 24.04 dependencies:
# g++ cmake make libboost-filesystem-dev libboost-program-options-dev
# libboost-iostreams-dev libboost-regex-dev libboost-locale-dev
# libmysqlclient-dev libssl-dev libreadline-dev libbz2-dev zlib1g-dev
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="${MOP_BUILD_DIR:-${source_dir}/../mop-build}"
install_dir="${MOP_INSTALL_DIR:-${source_dir}/../mop-install}"
cmake_bin="${CMAKE:-cmake}"
jobs="${MOP_BUILD_JOBS:-2}"

"${cmake_bin}" -S "${source_dir}" -B "${build_dir}" \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="${install_dir}" \
    -DPLAYERBOTS=ON -DELUNA=OFF -DUSE_MODULES=ON -DTOOLS=ON "$@"
"${cmake_bin}" --build "${build_dir}" --parallel "${jobs}"
"${cmake_bin}" --install "${build_dir}"
"${install_dir}/bin/authserver" --version
"${install_dir}/bin/worldserver" --version
