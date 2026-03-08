from setuptools import setup

setup(
    name="unicornhatmini",
    version="1.0.0",
    description="Optimized driver for Pimoroni Unicorn HAT Mini",
    packages=["unicornhatmini"],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "spidev",
    ],
)
