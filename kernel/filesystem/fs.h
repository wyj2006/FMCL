#pragma once

#include "fcb.h"

extern FCB *root;

void fs_init(std::vector<nfs::path> root_paths);
FCB *fs_load(std::string path);
void fs_service();