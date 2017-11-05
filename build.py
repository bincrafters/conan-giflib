from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager(args="--build missing")
    builder.add_common_builds(shared_option_name="giflib:shared", pure_c=True)
    if platform.system() == "Windows": # Library not prepared to create a .lib to link with (only dll)
        # Remove shared builds in Windows
        static_builds = []
        for build in builder.builds:
            if not build[1]["giflib:shared"]:
                static_builds.append([build[0], {}])
            
        builder.builds = static_builds
    builder.run()
