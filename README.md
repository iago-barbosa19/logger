# Logger

---
> O projeto serve para ser um logger próprio, tendo em vista que não sou muito fã do pacote logging.
> e tive a vontade de fazer esse projeto para aprender como um logger funciona.
>
> O projeto foi feito usando Python3.10 e bibliotecas nativas do Python, então é possível rodar em
> todas as versões do Python.

Para configurar o logger, é necessário criar um arquivo yml com nome: log_settings

A estrutura do arquivo deve ser a seguinte:

> log_level: "INFO"
> directory: "./logs"
> file_name: "log"
> size_limit: 512
> opening_method: "a+"
> encoding_method: "utf-8"

O arquivo não precisa ter os mesmos valores, mas precisa seguir o mesmo padrão.
