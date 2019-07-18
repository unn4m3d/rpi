Import("env")
from platformio import util
from platformio.project.helpers import get_project_build_dir, get_project_dir
from platformio.project.config import ProjectConfig
from os.path import basename, join, relpath, abspath, isfile, exists
from os import environ
import base64
import subprocess
import re

config = ProjectConfig.get_instance(join(get_project_dir(), "platformio.ini"))

def get_envname():
    return base64.b64decode(ARGUMENTS["PIOENV"])

envname = get_envname()
print("PBD: %s, env : %s" % (relpath(get_project_build_dir()), envname))

def get_option(section, option, dft):
    if config.has_option(section, option):
        return config.get(section, option)
    else:
        return dft

def get_env_option(name, default):
    return get_option("env:%s" % envname, name, default)

def get_crystal_target():
    return get_env_option("crystal_target", "main")

def get_crystal_build_flags():
    return get_env_option("crystal_build_flags", "")

def get_shards_binary():
    return get_env_option("crystal_shards_bin", "shards")

def get_crystal_binary():
    return get_env_option("crystal_bin", "crystal")

def get_crystal_triple():
    return get_env_option("crystal_arch", "arm-unknown-linux-gnueabihf")

def get_crystal_lib_path():
    return get_env_option("crystal_path_extra", "./lib")

def add_compile_crystal_target():
    input_file = get_crystal_target()
    output_obj_file = join(get_project_build_dir(), envname, "__crystal_{}".format(relpath(input_file)))
    print("output file : %s" % output_obj_file)

    shard_yml = isfile("shard.yml")
    linker_cmdline_file = join(get_project_build_dir(), envname, "__linker_cmd_{}".format(relpath(input_file)))

    sed_cmd = "sed -E -e 's/^.*-rdynamic//' -e 's/-L[^ ]+//g' -e 's/\/[^ ]+libcrystal.a//g'"

    compile = "{bin} build {crystal_target} --verbose -o{output} --cross-compile --target={target} {flags} | {sed} > {file}".format(
        bin = get_shards_binary() if shard_yml else get_crystal_binary(),
        crystal_target = input_file if shard_yml or isfile(input_file) else "src/%s.cr" % input_file ,
        output = output_obj_file,
        target = get_crystal_triple(),
        flags = get_crystal_build_flags(),
        file = linker_cmdline_file,
        sed = sed_cmd
    )

    output_obj_file = output_obj_file + ".o"

    install_shards = "{bin} update".format(bin = get_shards_binary())
    install_dep = None

    if shard_yml:
        env.AlwaysBuild(env.Alias("install_shards", None, [install_shards]))
        install_dep = "install_shards"

    env.Command(output_obj_file, install_dep, [compile])

    env.Depends("%s/%s/program" % (get_project_build_dir(), envname), output_obj_file)
    env.Append(PIOBUILDFILES=abspath(output_obj_file))

    libpath = join(get_crystal_lib_path(), "rpi", "libraries")
    local_libraries_exist = exists(join(get_project_dir(), "libraries"))
    local_libpath = " -L" + join(get_project_dir(), "libraries") if local_libraries_exist else ""
    env.Append(LINKFLAGS = "@%s -L%s%s" % (linker_cmdline_file, libpath, local_libpath))

def add_compile_crystal_extension():
    env.Append(SRC_FILTER="-<*/ext/sigfault.c>")
    libname = join(get_project_build_dir(), get_envname(), "crystal.o")
    env.Object(libname, ["src/ext/sigfault.c"])
    env.Append(LINKFLAGS=libname)
    env.Depends("%s/%s/program" % (get_project_build_dir(), envname), libname)

def export_crystal_path():
    if config.has_option("env:%s" % envname, "crystal_path_extra"):
        old_path = subprocess.check_output(['crystal', 'env', 'CRYSTAL_PATH']).rstrip()
        env.AppendENVPath('CRYSTAL_PATH', old_path )
        env.AppendENVPath('CRYSTAL_PATH', get_crystal_lib_path())
        print("CRYSTAL_PATH=%s" % env['ENV']['CRYSTAL_PATH'])

export_crystal_path()
add_compile_crystal_extension()
add_compile_crystal_target()
