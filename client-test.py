
import time
import librfap
import librfap.commands

client = librfap.Client("localhost")

client.rfap_ping()

print("asking for info on /")
client.send_command(librfap.commands.CMD_INFO, { "Path": "/" })
time.sleep(0.2)
_, _, header, _, body, _ = client.recv_command()
print("header is:", header)
print("body is:", body)

client.rfap_disconnect()

