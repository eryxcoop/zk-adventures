![Piezas_Crypto-07](https://github.com/user-attachments/assets/46205972-9536-4ce2-a47e-213d371703fa)

# ZK Adventures
First time:
```bash
docker run -v /global/path/to/zk-adventures:/home/sage/zk-adventures --name sage -p 8888:8888 sagemath/sagemath:latest sage-jupyter
```
Check out URL of the logs to navigate to the sage notebook: `http://127.0.0.1:8888/?token=some-random-token`

If you already ran the above you can open it back with

```bash
docker start sage
```

To recover the URL you can use (you may need to wait a bit after the command above)
```bash
docker logs sage
```


