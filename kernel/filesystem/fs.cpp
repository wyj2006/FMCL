#include <boost/log/attributes/constant.hpp>
#include <boost/log/attributes/scoped_attribute.hpp>
#include <boost/log/trivial.hpp>

#include <boost/algorithm/string.hpp>
#include <boost/asio.hpp>
#include <boost/json.hpp>
#include <boost/system.hpp>
#include <boost/thread.hpp>
#include <cstring>
#include <exception>
#include <vector>

#include "fs.h"

using boost::asio::ip::tcp;
namespace logging = boost::log;
namespace attrs = boost::log::attributes;

FCB *root = nullptr;

void fs_init(std::vector<nfs::path> root_paths) { root = new FCB("", root_paths); }

FCB *fs_load(std::string path)
{
    FCB *fcb;
    std::vector<std::string> names;
    boost::split(names, path, boost::is_any_of("/"), boost::token_compress_on);
    for (std::string name : names)
    {
        if (name == "")
            fcb = root;
        else
        {
            fcb->update_child(name);
            fcb = fcb->get_child(name);
            if (fcb == nullptr) return nullptr;
        }
    }
    return fcb;
}

void fs_service()
{
    BOOST_LOG_SCOPED_THREAD_ATTR("ThreadName", attrs::constant<std::string>("File System"));
    try
    {
        boost::asio::io_context io_context;
        tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), 1024));
        BOOST_LOG_TRIVIAL(info) << "Listening " << acceptor.local_endpoint();

        while (1)
        {
            tcp::socket socket(io_context);
            acceptor.accept(socket);
            BOOST_LOG_TRIVIAL(info) << "Connected " << socket.remote_endpoint();

            while (1)
            {
                std::array<char, 1024> buf;
                boost::system::error_code error;
                size_t len = socket.read_some(boost::asio::buffer(buf), error);
                buf[len] = '\0';
                if (error != boost::system::errc::success && error != boost::asio::error::eof)
                {
                    BOOST_LOG_TRIVIAL(error) << error.message();
                    BOOST_LOG_TRIVIAL(info) << "Disconnected(Because of error) " << socket.remote_endpoint();
                    socket.close();
                    break;
                }
                if (len == 0)
                {
                    BOOST_LOG_TRIVIAL(info) << "Disconnected " << socket.remote_endpoint();
                    socket.close();
                    break;
                }
                else if (!strncmp(buf.data(), "load", 4))
                {
                    std::string path(buf.data() + 5);
                    FCB *fcb = fs_load(path);

                    boost::json::object fileinfo;
                    if (fcb == nullptr)
                        fileinfo = {{"native_paths", boost::json::array()}};
                    else
                    {
                        boost::json::array native_paths;
                        for (auto path : fcb->native_paths) native_paths.emplace_back(path.string());
                        fileinfo = {
                            {"native_paths", native_paths},
                        };
                    }

                    boost::asio::write(socket, boost::asio::buffer(boost::json::serialize(fileinfo)), error);
                }
            }
        }
    }
    catch (std::exception &e)
    {
        BOOST_LOG_TRIVIAL(fatal) << e.what();
    }
}