with open('services/platform-service/entrypoint.sh', 'rb') as f:
    content = f.read()
content = content.replace(b'\r\n', b'\n')
with open('services/platform-service/entrypoint.sh', 'wb') as f:
    f.write(content)
print("Converted to LF")
