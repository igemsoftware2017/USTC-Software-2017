# Biohub 2.0 - iGem Project by USTC Software 2017

[![Build Status](https://travis-ci.org/igemsoftware2017/USTC-Software-2017.svg?branch=master)](https://travis-ci.org/igemsoftware2017/USTC-Software-2017)

## What is Biohub?

[Biohub](https://github.com/igemsoftware2016/USTC-Software-2016) is a web-based software authored by USTC Software 2016, focusing on more convenient data handling for synthetic biologists. Technically Biohub is a extensible plugin system, where each functional module is packed and integrated as a plugin. Several plugins (Pano, PathFinder, etc.) are initially included, but users are also allowed to develop and deploy their own plugins, with the help of documentation and demonstration. In this way, new algorithms can be acquainted and discussed by other scholars as early as possible.

## What is Biohub 2.0?

Biohub 2.0 is a synthetic biology community, focusing on more efficient data retrieving and ideas sharing. It provides a user-friendly interface to interact with standard biological parts, or BioBricks in short. With the help of a high-performance search backend and well-designed filtering and ordering algorithms, users can obtain information of the parts they want more precisely. For those interest them, users may leave a mark (called a 'Star') for later using. If one has already use a part in practice, he or she may grade the part, or post an article (called an 'Experience') to share ideas. Experiences can also be voted or discussed. All the data collected (rating scores, number of stars, etc.) will be used for more accurating filtering and ordering.

More than a community, Biohub 2.0 is also a flexible plugin system. A plugin is an optional and pluggable module that can be integrated into the software and take advantage of all the internal data. Plugin developers can either use BioBricks data for further analysis, or just implement a synthetic biological algorithm for the community. There is no specific restriction about the code of plugins, but they will be preapproved before installed into the system as a consideration of security. By default, two plugins, ABACUS and BioCircuit, are available as two handy tools and, in a sense, some kinds of demonstration.

Despite of the similarity in their names, Biohub 2.0 has few common points compared with Biohub. The two projects differ largely in their emphasis and implementation. The only thing Biohub 2.0 borrows from Biohub is the idea of the plugin system, which is further improved and implemented in a more stable way. The name 'Biohub', inspired by another active developer community Github, is very suitable for a biology community but was previously used. For disambiguation, the project is named Biohub 2.0.

## Motivation

The numerous parts provided by iGEM Parts Registry are precious to the community, but unfortunately displayed in a terrible way. For synthetic biologists with little or no knowledge about programming, the only approach to access the parts is by submitting the search box on the official pages, which is however too crude to use. The default matching algorithm defies multi-dimensional searching, and the default ordering is just wasting users' time. It's hopeless to get anything useful via this tool. Thus, a software to mine high-quality parts accurately is urgently needed.

With the data dumped from iGEM Parts Registry, which contains information like sample status or used times, the parts can be roughly ranked. But further ranking can only be accomplished after experiments are done, which requires the assistance from the whole community. Such feedback mechanism does exist in iGEM Parts Registry, which is called Experiences, but is seldom used probably because of its hard-to-use interface. We think a user-friendly forum centred on Biobricks is necessary, where users can grade the parts they've used, or share experiences with other scholars. The forum on the one hand complements the data used for more accurate ranking, and on the other hand provides a platform for idea exchanging.

The parts data can be used for various purposes, but apparently we are not able to achieve all of them. In consideration of this, we decide to make our software extensible. Developers with ideas to better make use of the data may develop their own plugins, and embed them into the software. With the help of forum, such plugins will be acquainted quickly, and accelerate the development of synthetic biology.

## How to use Biohub 2.0?

For biologists, just register an account on [biohub.technology](http://biohub.technology) and sign into it, and you can enjoy all the services we provide.

## How to develop a Biohub 2.0 plugin?

**NOTE** Since Biohub 2.0 has been developed, tested and deployed on Ubuntu 16.04, we recommend you to use similar working environment to avoid unexpected problems.

Firstly, you should make sure the following requirements are satisfied:

 + `python >= 3.5`. Related packages: `python3`, `python3.5-dev`. (`libbz2-dev`, `zlib1g-dev` are required if you compile python from source code).
 + `mysql >= 5.7`. Related packages: `mysql-server`, `mysql-client`, `libmysqlclient`.
 + `redis`. Related packages: `redis-server`.
 + `jre`. Related packages: `default-jre`.
 + `elasticsearch < 3`. Can be downloaded via: `https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.4.6/elasticsearch-2.4.6.deb`
 + `nodejs >= 6`. Related packages: `nodejs`.

Then you can clone down the repository by:

```bash
$ git clone https://github.com/igemsoftware2017/USTC-Software-2017
$ cd USTC-Software-2017
$ git submodule update --init --recursive
```

We recommend to use virtual environment to manage python dependencies:

```bash
$ python3 -m venv .env
$ source .env/bin/activate
(.env) $ pip install -r requirements/dev.txt
```

### Setting up the server

The main configuration file should lie at `~/config.json`. You can finish it with the help of `~/config.json.example`:

```javascript
{
    "DATABASE": {
        "NAME": "",     // database name
        "USER": "",     // database username
        "PASSWORD": "", // database password
        "HOST": "",     // database host, here should be "localhost"
        "PORT": 3306,   // database port
        "TEST": {       // test database
            "NAME": "",
            "CHARSET": "utf8",
            "COLLATION": null,
            "MIRROR": null
        }
    },
    "PLUGINS": [        // list of installed plugins
        "biohub.abacus",
        "biohub.biocircuit",
        "biohub.biomap"
    ],
    "TIMEZONE": "UTC",
    "UPLOAD_DIR": "",   // path to directory where uploaded files are placed
    "REDIS_URI": "",    // redis connection URL. format "redis://<username>:<password>@<host>:6379"
    "SECRET_KEY": "",   // secret key of the site
    "MAX_TASKS": 20,    // the maximum number of tasks can be executed at a time
    "TASK_MAX_TIMEOUT": 180,  // the maximum seconds a task can be executed
    "ES_URL": "http://127.0.0.1:9200/", // the connection URL of ElasticSearch
    "EMAIL": {          // email configuration
        "HOST_PASSWORD": "",
        "HOST_USER": "",
        "HOST": "",
        "PORT": 465
    },
    "CORS": [],         // authenticated domains. fill the field if cross-domain issues occur during debugging
    "THROTTLE": {       // throttle configuration for each modules
        "rate": 15,
        "experience": 86400,
        "post": 15,
        "vote": 15,
        "register": 3600
    }
}
```

Then run `./biohub-cli.py init` to initialize the database. This step may take several minutes as it will download and preprocess the initial data. After that you can run `./biohub-cli.py runserver` to test if the server can be normally started.

### Setting up the frontend

The frontend of Biohub 2.0 lies in `frontend/main`. Firstly you should install the dependencies:

```bash
$ cd frontend/main
$ npm install
```

During developing, Biohub 2.0 uses `webpack-dev-server` for hot-reloading. You should configure the proxies in `frontend/main/domain.config.json` to make it work properly. As above, an example file is available:

```javascript
{
    "dev": {
        // during developing, plugins and the main frontend are compiled and served separately
        // the following field maps each plugin to a port where its frontend files served
        // to serve a plugin frontend files, run `npm run dev <port>` in its frontend directory
        "plugins": {
            "biohub.abacus": 10000,
            "biohub.biocircuit": 10001,
            "biohub.biomap": 10002
        },
        // the address to your local developing server
        "proxy_domain": "localhost:8000"
    },
    // configuration for production environment
    // you can simply ignore it
    "prod": {
        "domain": "biohub.technology",
        "static": "https://ustc-software2017-frontend.github.io/Biohub-frontend/dist/assets/"
    }
}
```

Then run `npm run dev`, and you can access the site at `localhost:8080`.

### Create your own plugin

To create and activate a new plugin, simply run:

```bash
(.env) $ ./biohub-cli.py plugin new <plugin_name> --with-frontend
(.env) $ ./biohub-cli.py plugin install <plugin_name>
```

where `<plugin_name>` is the **dot-separated module name** of the plugin (e.g. `biohub.abacus`). You may type `./biohub-cli.py plugin new --help` to find more details.

The second step is to install dependencies for the frontend of the new plugin. Simply run:

```bash
(.env) $ cd path/to/your/plugin/frontend
(.env) $ npm install
(.env) $ npm run dev <port>  # randomly choose a number for <port> from 10000~65535
```

Then compiled files will be served at `localhost:<port>`. Don't forget to add a new item in `frontend/main/domain.config.json`:

```javascript
{
    "dev": {
        // ...
        plugins: {
            // ...
            "<your_plugin_name>": "<port>"
        }
    }
}
```

Now you can start to write your own plugin. The templates generated by `biohub-cli` contains some useful comments, which may help you during developing. Also, you can take our integrated plugins (e.g. `biohub.biomap`) as references.
