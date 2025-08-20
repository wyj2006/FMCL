#pragma once
#define WIN32_LEAN_AND_MEAN

#include <boost/process.hpp>
#include <string>
#include <vector>

#include "directory.h"

namespace bp = boost::process;

class Function : public Directory {
public:
    Function(std::string path) : Directory(path) {}

    bp::process *run(std::vector<std::string> args = {});
};