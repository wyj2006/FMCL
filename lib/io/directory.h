#pragma once

#include "file.h"

class Directory : public File {
public:
    Directory(std::string path) :
        File(path) {}
};