/***************************************************************************
 *  This is a simple c++ macro-based log model.
 *  Author: How Zheng
 *  Data : 2020/12/18
 * *************************************************************************/

#ifndef _HOW_LOG_H_
#define _HOW_LOG_H_

#include <cstring>
#include <iostream>
#include <string_view>
#include <array>

enum Log_level
{
    L_ERROR = 0,
    L_INFO = 1,
    L_DEBUG = 2
};

static Log_level LOG_LEVEL = L_INFO;

static constexpr std::array log_colors 
{
    "\u001b[31m",
    "\u001b[32m",
    "\u001b[33m", 
};

void SET_LOG(Log_level level);


template<typename... Args>
void OUT_LOG(const Log_level level, const std::string_view s, Args... args)
{
    std::FILE* output = (level == L_ERROR ? stderr : stdout);
    if (level <= LOG_LEVEL)
    {
        std::fprintf(output, "%s", log_colors[level]);
        switch(level){
            case L_INFO:
                std::fprintf(output, "[INFO] ");
                break;
            case L_DEBUG:
                std::fprintf(output, "[DEBUG] ");
                break;
            case L_ERROR:
                std::fprintf(output, "[ERROR] ");
                break;
        }
        std::fprintf(output, std::string(s).c_str(), args...);
        std::fprintf(output, "\x1B[0m");
        std::fprintf(output, "\n");
    }
}

# define __FILENAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)
# define HOW_LOG(lvl, msg, ...)  { OUT_LOG(lvl, "[%s:%d] " msg, __FILENAME__, __LINE__, ##__VA_ARGS__); } (void)0

#endif