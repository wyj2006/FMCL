#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "zip.h"
#include <string.h>
#include <wchar.h>

#if _WIN32 || _WIN64

#include <direct.h>
#include <io.h>
#include <shlwapi.h>
#include <windows.h>

#define setenv _putenv_s

void dirname(char *path)
{
    for (size_t i = strlen(path) - 1; i > 0; i--)
    {
        if (path[i] == '/' || path[i] == '\\')
        {
            path[i] = '\0';
            break;
        }
    }
}

/*获取可执行文件的路径*/
void get_executable_path(char *buf, size_t size)
{
    GetModuleFileName(NULL, buf, size);
    dirname(buf); // PathRemoveFileSpec(buf);
}

#elif __linux__

#include <libgen.h>
#include <unistd.h>

/*获取可执行文件的路径*/
void get_executable_path(char *buf, size_t size)
{
    readlink("/proc/self/exe", buf, size);
    dirname(buf);
}

#else
#error 暂时不支持的操作系统
#endif

#define FATAL_ERROR(msg, ...)                                                  \
    do                                                                         \
    {                                                                          \
        printf("Error: ");                                                     \
        printf(msg, __VA_ARGS__);                                              \
        printf("\n\tat %s:%d\n", "kernel/main.c", __LINE__);                   \
        Py_Exit(1);                                                            \
    } while (0)

char executable_path[1024];

const char env_zip[] = {
#embed "env.zip"
};

int on_extract_entry(const char *filename, void *arg)
{
    static int i = 0;
    printf("[%d] Extracted: %s\n", ++i, filename);
    return 0;
}

void decompress_env()
{
    errno_t err;
    char dir[1024];
    strcpy_s(dir, sizeof(dir), executable_path);
    strcat_s(dir, sizeof(dir), "/FMCL");

    char env_zip_path[1024];
    strcpy_s(env_zip_path, sizeof(env_zip_path), dir);
    strcat_s(env_zip_path, sizeof(env_zip_path), "/env.zip");

    if (_access(env_zip_path, 0) == 0) return;

    err = zip_stream_extract(env_zip, sizeof(env_zip), dir, on_extract_entry,
                             NULL);
    if (err != 0)
        FATAL_ERROR("Cannot extract '%s' [Error code %d]", env_zip_path, err);

    FILE *zip_file;
    if (!fopen_s(&zip_file, env_zip_path, "wb"))
    {
        fwrite(env_zip, sizeof(char), sizeof(env_zip), zip_file);
        fclose(zip_file);
    }
}

void init()
{
    wchar_t wc_exec_path[1024];
    for (size_t i = 0, j = 0; i < strlen(executable_path); i++, j++)
    {
        int len = mbtowc(&wc_exec_path[j], executable_path + i, MB_CUR_MAX);
        if (len > 0) i += len - 1;
        wc_exec_path[j + 1] = '\0';
    }

    PyStatus status;

    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    status = PyConfig_SetBytesString(&config, &config.program_name, "FMCL");
    if (PyStatus_Exception(status)) goto exception;

    wchar_t home_path[1024];
    wcscpy(home_path, wc_exec_path);
    wcscat(home_path, L"/FMCL");
    status = PyConfig_SetString(&config, &config.home, home_path);
    if (PyStatus_Exception(status)) goto exception;

    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) goto exception;

    PyConfig_Clear(&config);
    return;
exception:
    PyConfig_Clear(&config);
    Py_ExitStatusException(status);
}

int main(int argc, char *argv[])
{
    get_executable_path(executable_path, sizeof(executable_path));
    decompress_env();
    init();
    PyRun_InteractiveLoop(stdin, "<string>");
    Py_Finalize();
    return 0;
}