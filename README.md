# ReadService

**ReadService** это MVP сервиса pipeline загрузки документов в векторную БД для RAG
---

## 🚀 Features
- 🧪 Реализован с использованием фреймворка LangChain
- 📁 Поддерживает два источника файлов: локальная папка (volumeMount длф контейнера) and S3-совместимый сервис (протестирован с minIO).
- 📄 Поддерживает загрузку различных типов файлов: TXT, CSV, PDF, DOCX, XLSX, HTML, PPTX
- 🧠 Использует расширяемый набор Loaders и Splitters из набора LangChain (см. ниже)
- 🔎 Embedding реализовн с помощью вызова модели (расширяемый набор) (работает с YandexGPT, LiteLLM + YandexGPT, также есть две "заглушки").
- 🗄️ Для сохранения использует **Milvus** или **PGVector**. Работает со структурой данных по-умолчанию от LangChain
- ⚙️ Настройки по-умолчанию хранятся в `config.yaml`, переопределяются или расширяются через переменные environment (префикс `RS__`).
- 🐳 Запускается через командныю строку, череза Docker образ, или через Kubernetes CronJob.

---

## 🧩 Архитектура / Pipeline

```
        +-----------+
        |  Sources  | <--- "Локальные" папки, S3 buckets
        +-----------+       файлы загружаются по списку поддерживаемых расшиений из конфигурации в `config.yaml`
              |
              v
       +---------------+
       |  Loaders      | <--- PDFPlumberLoader, Docx2txtLoader, TextLoader, UnstructuredWordDocumentLoader, CSVLoader, UnstructuredHTMLLoader,  
       +---------------+      UnstructuredExcelLoader, PyMuPDFLoader, BSHTMLLoader, UnstructuredPowerPointLoader
              |
              v
      +------------------+
      |  Splitters       | <--- RecursiveCharacterTextSplitter, TokenTextSplitter, NLTKTextSplitter, SpacyTextSplitter
      +------------------+      Т.к. Loader может вернуть текст файла уже побитого на части, можно установить тип splitter: none
              |
              v
      +------------------+
      |  Embeddings      | <--- YandexGPT, LiteLLM, Fake...
      +------------------+      embedding вызывается средствами LangChain непосредственно при сохранении в БД
              |
              v
      +------------------+
      |  Vector Stores   | <--- Milvus, PGVector
      +------------------+      сохраняются также метаданные, включая hashcode, назвние и размер файла источника и др.
```

## ⚙️ Конфигурация

- `config.yaml` настройки по-умолчанию
- `RS__`- environment переменные (совместиые с docker env) для изменения/расширения настроек по-умолчанию

Пример переменных для "локального" запуска:
```bash
export RS__EMBEDDING__YANDEXGPT__API_KEY=your-secret-key
export RS__SOURCES__USE_LOCAL=true
python -m readservice.main
```

Названия environment переменных получаются путем преобразования структуры `config.yaml`

в `config.yaml`:
storage:
  store_type: pgvector # "milvus" or "pgvector"

соответствующая environment переменная: 
RS__STORAGE__STORE_TYPE

Опционально можно расширять существующие пареметры `config.yaml`через "новые" параметры в environment, например для добавления параметров Splitter-а, которых нет в `config.yaml`
```bash
export RS__SPLITTERS__TOKENTEXTSPLITTER__DISALLOWED_SPECIAL=all
```

## 🐳 Deployment

### Docker Image

- Сборка образа:
  ```bash
  docker build --pull --rm -f 'readservice/Dockerfile' -t 'readservice:latest' 'readservice'
  ```
- Пример запуска:
  ```bash
  docker run --rm -it -e "RS__EMBEDDING__PROVIDER=yandexGPT" -e "RS__EMBEDDING__YANDEXGPT__API_KEY=********" -e "RS__EMBEDDING__YANDEXGPT__FOLDER_ID=********" -e "RS__SOURCES__USE_LOCAL=true" -e "RS__SOURCES__USE_S3=true" -e "RS__STORAGE__STORE_TYPE=milvus" -e "RS__DELETE_OLD_VECTORS=true" -v /home/local_docs:/app/local_docs readservice:latest /bin/bash

  python -m readservice.main
  ```
Без задания environment переменных сервис будет запущен с параметрами по-умолчанию из `config.yaml`

---

### Kubernetes CronJob
пример в папке `example`

---

### Создание Helm Chart-а возможно через сервис-шаблонизатор
шаблон в папке `metamart`

---

## 🏁 Локальный запуск

```bash
python -m readservice.main
```
Без задания envirinment переменных сервис будет запущен с параметрами по-умолчанию из `config.yaml`

---

## 📝 TODO

- Уменньшить размер собираемого docker образа
- Добавить модели для embedding-а 
- Добавить возможность загрузки web-сайтов 
- Добавить unit тесты
- ...