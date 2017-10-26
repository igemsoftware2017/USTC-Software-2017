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

For biologists, just register an account on [biohub.tech](http://biohub.tech) (not deployed yet) and sign into it, and you can enjoy all the services we provide.

For plugin developers, it's recommended to read our [Tutorials](#) (not deployed yet) first to get an idea of the plugin model. The documantation also contains [full list of references for Plugin APIs](#) (not deployed yet).

If you are interested in the implementation of Biohub 2.0, you may also clone this repository onto your server and run it. The documantation contains a guide on [how to deploy this project](#) (not deployed yet). But **NOTE** that Biohub 2.0 is a GPL-licensed project, so all you have done with it must not violate the license.
