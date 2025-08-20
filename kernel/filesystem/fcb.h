#pragma once

#include <boost/filesystem.hpp>
#include <string>
#include <vector>

namespace nfs = boost::filesystem; // Native File System

class FCB {
public:
    std::string name;
    std::vector<nfs::path> native_paths; // 一个FCB可以对应多个实际路径
    FCB *parent;
    std::vector<FCB *> childs;

    FCB(std::string name, std::vector<nfs::path> native_paths,
        FCB *parent = nullptr);
    FCB *get_child(std::string name);
    void update_child(std::string name);
};