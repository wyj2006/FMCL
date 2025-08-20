#include <boost/log/trivial.hpp>

#include <boost/asio.hpp>
#include <boost/json.hpp>
#include <boost/system/detail/errc.hpp>
#include <cstring>
#include <exception>

#include "file.h"

using boost::asio::ip::tcp;

File::File(std::string path) : path(path)
{
    boost::asio::io_context io_context;
    tcp::resolver resolver(io_context);
    tcp::resolver::results_type endpoints = resolver.resolve("127.0.0.1", "1024");
    tcp::socket socket(io_context);
    boost::asio::connect(socket, endpoints);

    std::array<char, 1024> buf;
    boost::system::error_code error;

    boost::asio::write(socket, boost::asio::buffer("load " + path), error);
    if (error) throw std::exception(error.message().data());

    size_t len = socket.read_some(boost::asio::buffer(buf), error);
    if (error) throw std::exception(error.message().data());

    buf[len] = '\0';
    auto fileinfo = boost::json::parse(buf.data()).as_object();
    for (auto path : fileinfo["native_paths"].as_array()) native_paths.push_back(path.as_string().data());

    socket.close();
}
