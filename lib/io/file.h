#pragma once

#include <boost/filesystem.hpp>
#include <string>
#include <vector>

namespace nfs = boost::filesystem; // Native File System

class File {
public:
    std::string path;
    std::vector<nfs::path> native_paths;

    File(std::string path);

    bool exist() { return native_paths.size() != 0; }
};