FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# texlive-latex-extra: for common packages (geometry, booktabs, etc.)
# texlive-lang-polish: for Polish language support (babel)
# texlive-pictures: for tikz
# python3-pip: for python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-lang-polish \
    texlive-pictures \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Make script executable
RUN chmod +x run_pipeline.sh

# Default command
CMD ["./run_pipeline.sh"]
