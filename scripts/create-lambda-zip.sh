#!/usr/bin/env bash

LastVersion=1

[ ! -d $LastVersion ] && mkdir $LastVersion
mkdir $LastVersion/lambda
mkdir $LastVersion/lambda/layers
cd ../lambda

# developer portal management lambda
zip ../scripts/$LastVersion/lambda/DeveloperPortalManagement.zip DeveloperPortalManagement.py


