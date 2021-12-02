
import librfap
import librfap.commands

client = librfap.Client("localhost")

client.rfap_ping()

print("asking for info on /")
header = client.rfap_info("/", True)
print("resp:", header)

#_, files = client.rfap_directory_read("/")
#for i in files:
#    metadata = client.rfap_info("/" + i)
#    print(metadata)

client.rfap_disconnect()

