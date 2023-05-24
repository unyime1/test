FROM python:3.11-slim

# Only update packages
RUN apt-get update

# Set working directory
WORKDIR /account

# copy requirements files
COPY ./requirements.txt /account/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# Copy codebase
COPY . /account/

# create a new user
RUN adduser --disabled-password --gecos '' clip

# Set user as the owner of the account directory
RUN chown -R clip:clip /account

# Set user to be clip
USER clip
