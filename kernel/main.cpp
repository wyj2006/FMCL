#include <boost/log/attributes.hpp>
#include <boost/log/attributes/scoped_attribute.hpp>
#include <boost/log/core.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/expressions/attr.hpp>
#include <boost/log/sinks/sync_frontend.hpp>
#include <boost/log/sinks/text_ostream_backend.hpp>
#include <boost/log/sources/basic_logger.hpp>
#include <boost/log/sources/record_ostream.hpp>
#include <boost/log/sources/severity_channel_logger.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/support/date_time.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/utility/value_ref.hpp>

#include <boost/core/null_deleter.hpp>
#include <boost/date_time/posix_time/ptime.hpp>
#include <boost/smart_ptr/shared_ptr.hpp>
#include <boost/thread.hpp>
#include <exception>
#include <iostream>
#include <ostream>
#include <string>

#include "filesystem/fs.h"
#include "io/function.h"

namespace logging = boost::log;
namespace expr = boost::log::expressions;
namespace sinks = boost::log::sinks;
namespace attrs = boost::log::attributes;

BOOST_LOG_ATTRIBUTE_KEYWORD(thread_name, "ThreadName", std::string)

int main()
{
    logging::formatter fmt =
        expr::stream << "[" << expr::format_date_time<boost::posix_time::ptime>("TimeStamp", "%Y-%m-%d %H:%M:%S")
                     << "] [" << thread_name << "/" << expr::attr<logging::trivial::severity_level>("Severity")
                     << "]: " << expr::smessage;

    typedef sinks::synchronous_sink<sinks::text_ostream_backend> console_sink;
    boost::shared_ptr<console_sink> sink = boost::make_shared<console_sink>();

    sink->locked_backend()->add_stream(boost::shared_ptr<std::ostream>(&std::clog, boost::null_deleter()));
    sink->set_formatter(fmt);
    logging::core::get()->add_sink(sink);

    logging::add_common_attributes();

    BOOST_LOG_SCOPED_THREAD_ATTR("ThreadName", attrs::constant<std::string>("Main"));

    try
    {
        fs_init({".."});

        boost::thread fs_server(&fs_service);

        Function explorer("/functions/explorer");

        bp::process *explorer_proc = explorer.run();

        fs_server.join();
    }
    catch (std::exception &e)
    {
        BOOST_LOG_TRIVIAL(fatal) << e.what();
    }
}