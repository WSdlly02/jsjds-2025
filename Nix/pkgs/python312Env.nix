{
  extraPackages ? [ ],
  inputs,
  python312,
  system,
}:
python312.withPackages (
  python312Packages: # just formal arguement
  with python312Packages;
  with inputs.self.legacyPackages."${system}";
  [
    # Drivers from self
    mlx90460-driver.Adafruit-Blinka
    mlx90460-driver.adafruit-circuitpython-busdevice
    mlx90460-driver.adafruit-circuitpython-connectionmanager
    mlx90460-driver.adafruit-circuitpython-mlx90640
    mlx90460-driver.adafruit-circuitpython-requests
    mlx90460-driver.adafruit-circuitpython-typing
    mlx90460-driver.rpi-ws281x
    ncnn
    picamera2
    pidng
    simplejpeg
    v4l2-python3
    # Drivers converted from normal derivations
    libcamera
    rpi-kms
    # Drivers from Nixpkgs
    adafruit-platformdetect
    adafruit-pureio
    av
    binho-host-adapter
    piexif
    pillow
    pyftdi
    pyserial
    python-prctl
    pyusb
    rpi-gpio
    sysv-ipc
    typing-extensions
    # Daily runtimes
    flask
    opencv4
    numpy
    psutil
    pyinstaller
    waitress # Web Server
    ultralytics # YOLO
  ]
  ++ extraPackages
)
