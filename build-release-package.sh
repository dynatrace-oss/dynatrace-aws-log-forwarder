#!/bin/bash
#   Copyright 2021 Dynatrace LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

LAMBDA_BUILD_DIR="temp-package-build"
LAMBDA_ZIP_NAME="dynatrace-aws-log-forwarder-lambda.zip"

PACKAGE_BUILD_DIR="dynatrace-aws-log-forwarder"
PACKAGE_ZIP_NAME="dynatrace-aws-log-forwarder.zip"

set -ex

rm -f $LAMBDA_ZIP_NAME
rm -rf $LAMBDA_BUILD_DIR


# PREPARE LAMBDA ZIP

mkdir $LAMBDA_BUILD_DIR
sh version.sh

# add lambda source
cp -r src/* $LAMBDA_BUILD_DIR

# add dependencies
pip3 install -r src/requirements.txt --target $LAMBDA_BUILD_DIR

# create lambda ZIP
cd $LAMBDA_BUILD_DIR
zip -r ../$LAMBDA_ZIP_NAME *
cd ..
rm -rf $LAMBDA_BUILD_DIR


# PREPARE WHOLE PACKAGE ZIP

mkdir $PACKAGE_BUILD_DIR

cp README.md dynatrace-aws-logs.sh $LAMBDA_ZIP_NAME dynatrace-aws-log-forwarder-template.yaml $PACKAGE_BUILD_DIR
cd $PACKAGE_BUILD_DIR
zip ../$PACKAGE_ZIP_NAME *
cd ..

rm -rf $PACKAGE_BUILD_DIR
