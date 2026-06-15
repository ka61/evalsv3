# Base on the Inspect tool-support image so bash/python/editor tools work,
# then add pytest so the scorer can run the test suite.
FROM aisiuk/inspect-tool-support
RUN pip install --no-cache-dir pytest
WORKDIR /workspace
