
import librfap
import librfap.commands

client = librfap.Client("localhost")

client.rfap_ping()

client.send_command(librfap.commands.CMD_INFO, { "Path": "/" })
_, _, header, _, body, _ = client.recv_command()
print("header is:", header)
print("body is:", body)

client.rfap_disconnect()

