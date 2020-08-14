# Manylinux web builder

## First run

- Create many_local image
```bash
docker build -t many_local manylinux
```

- Run the stack
```bash
# Create packages folder
mkdir packages
chmod -R 777 packages
docker-compose up
```

- You can use for testing: https://github.com/afreydev/hello.git