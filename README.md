# Quick Start Guide

This guide will help you set up your environment quickly and run the provided test cases.

---

## 1. Setup Executable Permissions

Make the script executable by running:

```bash
chmod +x scripts/minio/init-bucket.sh
```

---

## 2. Start Docker Containers

### Start in Detached Mode

Run the following command to start the containers in the background:

```bash
docker compose up -d
```

### Start with Logs

If you want to see the logs in real time, use:

```bash
docker compose up
```

---

## 3. Stop and Clean Up

To stop the containers and remove all associated volumes, run:

```bash
docker compose down -v
```

---

## 4. Access MinIO (S3 Simulation)

Open your browser and navigate to:

```
http://localhost:9001/
```

Use the following credentials to log in:

- **Username:** minio-access-key
- **Password:** minio-secret-key

---

## 5. Run Test Cases

Set the `PYTHONPATH` to the current directory and run your tests using pytest:

```bash
export PYTHONPATH=$(pwd)
pytest -v
```