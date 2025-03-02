cp -r ../common_avito_utils src/deps/common_avito_utils_tmp
docker build -t avito_user_asker_service .
rm -rf src/deps/common_avito_utils_tmp