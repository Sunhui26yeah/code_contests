# ============================================================
# WORKSPACE — fully unified Protobuf (v3.19.3)
# ============================================================

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

# 1️⃣  Fix and pre-register protobuf BEFORE any other deps
git_repository(
    name = "com_google_protobuf",
    remote = "https://github.com/protocolbuffers/protobuf.git",
    tag = "v3.19.3",         # last Riegeli-safe version
)

# Provide @protobuf alias immediately so Riegeli/grpc cannot spawn protobuf~
local_repository(
    name = "protobuf",
    path = "external/com_google_protobuf",
)



# ============================================================
# 2️⃣  gRPC (uses maybe(), respects existing protobuf)
# ============================================================
git_repository(
    name = "com_github_grpc_grpc",
    remote = "https://github.com/grpc/grpc.git",
    commit = "aea02409bb9a60f838e09f422ea04ec36c58c04a",
)
load("@com_github_grpc_grpc//bazel:grpc_deps.bzl", "grpc_deps")
grpc_deps()

# ============================================================
# 3️⃣  Python / Abseil / GTest
# ============================================================
git_repository(
    name = "rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    tag = "0.5.0",
)

git_repository(
    name = "com_google_absl",
    remote = "https://github.com/abseil/abseil-cpp.git",
    tag = "20211102.0",
)

git_repository(
    name = "com_google_googletest",
    remote = "https://github.com/google/googletest.git",
    tag = "release-1.10.0",
)

# ============================================================
# 4️⃣  Riegeli (needs protobuf unification)
# ============================================================
http_archive(
    name = "com_google_riegeli",
    sha256 = "059af80271b6e62df2662fbf0d1d2724a8eaf881d16459d59d4025132126672c",
    strip_prefix = "riegeli-75aa942e1ddb5830eadac06339cfd4eb740da6f6",
    url = "https://github.com/google/riegeli/archive/75aa942e1ddb5830eadac06339cfd4eb740da6f6.tar.gz",
)

# ============================================================
# 5️⃣  Remaining third-party libs (same as your originals)
# ============================================================
http_archive(
    name = "org_brotli",
    sha256 = "fec5a1d26f3dd102c542548aaa704f655fecec3622a24ec6e97768dcb3c235ff",
    strip_prefix = "brotli-68f1b90ad0d204907beb58304d0bd06391001a4d",
    urls = ["https://github.com/google/brotli/archive/68f1b90ad0d204907beb58304d0bd06391001a4d.zip"],
)

http_archive(
    name = "net_zstd",
    build_file = "//third_party:net_zstd.BUILD.bazel",
    sha256 = "b6c537b53356a3af3ca3e621457751fa9a6ba96daf3aebb3526ae0f610863532",
    strip_prefix = "zstd-1.4.5/lib",
    urls = ["https://github.com/facebook/zstd/archive/v1.4.5.zip"],
)

http_archive(
    name = "snappy",
    build_file = "//third_party:snappy.BUILD.bazel",
    sha256 = "38b4aabf88eb480131ed45bfb89c19ca3e2a62daeb081bdf001cfb17ec4cd303",
    strip_prefix = "snappy-1.1.8",
    urls = ["https://github.com/google/snappy/archive/1.1.8.zip"],
)

http_archive(
    name = "crc32c",
    build_file = "//third_party:crc32.BUILD.bazel",
    sha256 = "338f1d9d95753dc3cdd882dfb6e176bbb4b18353c29c411ebcb7b890f361722e",
    strip_prefix = "crc32c-1.1.0",
    urls = ["https://github.com/google/crc32c/archive/1.1.0.zip"],
)

http_archive(
    name = "zlib",
    build_file = "//third_party:zlib.BUILD.bazel",
    sha256 = "c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1",
    strip_prefix = "zlib-1.2.11",
    urls = ["http://zlib.net/fossils/zlib-1.2.11.tar.gz"],
)

http_archive(
    name = "highwayhash",
    build_file = "//third_party:highwayhash.BUILD.bazel",
    sha256 = "cf891e024699c82aabce528a024adbe16e529f2b4e57f954455e0bf53efae585",
    strip_prefix = "highwayhash-276dd7b4b6d330e4734b756e97ccfb1b69cc2e12",
    urls = ["https://github.com/google/highwayhash/archive/276dd7b4b6d330e4734b756e97ccfb1b69cc2e12.zip"],
)

http_archive(
    name = "com_google_farmhash",
    build_file = "//third_party:farmhash.BUILD",
    sha256 = "6560547c63e4af82b0f202cb710ceabb3f21347a4b996db565a411da5b17aba0",
    strip_prefix = "farmhash-816a4ae622e964763ca0862d9dbd19324a1eaf45",
    urls = ["https://github.com/google/farmhash/archive/816a4ae622e964763ca0862d9dbd19324a1eaf45.tar.gz"],
)

# ============================================================
# 6️⃣  Sandboxed-API (transitively uses protobuf)
# ============================================================
maybe(
    git_repository,
    name = "com_google_sandboxed_api",
    commit = "10c04ed42f51dee1fa5f145e86ca3658a3876cfa",
    remote = "https://github.com/google/sandboxed-api.git",
)
load("@com_google_sandboxed_api//sandboxed_api/bazel:sapi_deps.bzl", "sapi_deps")
sapi_deps()

# ============================================================
# 7️⃣  Explicit protobuf dependency wiring
# ============================================================
load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
protobuf_deps()

# ============================================================
# ✅  Optional fallback patch (only used if protobuf~ reappears)
# ============================================================
# new_local_repository(
#     name = "fix_riegeli_protobuf",
#     build_file = "//third_party:fix_riegeli_protobuf.BUILD.bazel",
#     path = ".",
# )
# ============================================================
# End of WORKSPACE
# ============================================================
