import board
import digitalio
import busio

print("BLINKA")

pin = digitalio.DigitalInOut(board.D4)
print("IO Ok")

i2c = busio.I2C(board.SCL, board.SDA)
print("I2C Ok")

print("done")
