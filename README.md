# ml-microdep

# my-py
Can be used to type check python scripts during runtime.
my-py linter works in editor

# .env

# folder structure
```bash
├─ /home/emilte/ # working directory until project is adapted by Uninett (up)
│   ├─ ml-microdep/ # repository
│       ├─ ... # other dirs/files in ml-microdep
│
│       ├─ dynga_data_temp/ # local temp dir with same structure as /dynga/data/
│           ├─ dragonlab/
│               ├─ host/
│                   ├─ yyyy.mm.dd/
│                       ├─ crude.gz
│                       ├─ traceroute.gz
│                       ├─ gaps
│                       ├─ ... # other log files
│                   ├─ ... # other days
│               ├─ ... # other hosts
│
│           ├─ uninett/
│               ├─ host/ # ngu-mp.ngu.no
│                   ├─ yyyy.mm.dd/
│                       ├─ crude.gz
│                       ├─ traceroute.gz
│                       ├─ gaps # file made by this project
│                       ├─ ... # other log files
│                   ├─ ... # other days
│               ├─ ... # other hosts
```
