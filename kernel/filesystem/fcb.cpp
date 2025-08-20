#include <algorithm>

#include "fcb.h"

FCB::FCB(std::string name, std::vector<nfs::path> native_paths, FCB *parent) : name(name), native_paths(native_paths)
{
    this->parent = parent;
}

FCB *FCB::get_child(std::string name)
{
    for (FCB *child : childs)
        if (child->name == name) return child;
    return nullptr;
}

void FCB::update_child(std::string name)
{
    for (nfs::path native_path : native_paths)
    {
        for (auto &entry : nfs::directory_iterator(native_path))
        {
            if (entry.path().filename() == name)
            {
                FCB *child = get_child(name);
                if (child == nullptr)
                    childs.push_back(new FCB(name, {entry.path()}, this));
                else if (std::count(child->native_paths.begin(), child->native_paths.end(), entry.path()) == 0)
                    child->native_paths.push_back(entry.path());
            }
        }
    }
}