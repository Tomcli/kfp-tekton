#!/bin/bash
#
# Copyright 2020 kubeflow.org
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script checks whether the files listed in $files_to_check have been 
# Check if files affecting backend docker build have been modified from master.
# Only execute from kfp-tekton/

set -e

DIFF_DETECTED_ERR_CODE=${DIFF_DETECTED_ERR_CODE:-169}

pushd backend > /dev/null

org="kubeflow"
repository="kfp-tekton"
git_url="git://github.com/${org}/${repository}.git"

latest_commit=$(git ls-remote ${git_url} | grep HEAD | cut -f 1)

dockerfiles=(`ls Dockerfile*`)
files_to_check=(${dockerfiles} src)

for file in $files_to_check
do
    diff_output=$(git diff ${latest_commit} HEAD -- $file)
    if [[ -n "${diff_output}" ]]
    then
        echo "diff detected in $file"
        exit DIFF_DETECTED_ERR_CODE
    fi
done

popd > /dev/null

exit 0

# TODO
# exit code for: when we detect file change and must run test, no file change and skip test, other error and fail test
# add to travis https://travis-ci.community/t/how-to-skip-jobs-based-on-the-files-changed-in-a-subdirectory/2979/12
# test by modifying and committing a file
# remove garbage from files to check!!!