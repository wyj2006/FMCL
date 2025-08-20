#include <boost/log/trivial.hpp>

#include <boost/asio.hpp>

#include "function.h"

namespace asio = boost::asio;

bp::process *Function::run(std::vector<std::string> args)
{
    BOOST_LOG_TRIVIAL(info) << "Running " << path;
    // TODO 不只限于Python
    std::vector<std::string> full_args;
    full_args.push_back("__main__.py");
    full_args.insert(full_args.end(), args.begin(), args.end());

    asio::io_context ctx;

    bp::process *process =
        new bp::process(ctx.get_executor(), bp::environment::find_executable("py"), full_args,
                        bp::process_start_dir(native_paths[0]));

    return process;
}