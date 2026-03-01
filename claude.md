### Project Overview

This is a cross-platform customized project. As an overview, the project actively monitors the currently browsing website in a customized interval (maybe 30s to 1min). For the browsed website, the project will record the last dozens of them (maybe 100, tunable). Then, it uses html2md tools to conver the html content to markdown format, preserving the key information which is LLM-friendly. After that, the latest website is synced up to my desktop server via ssh (192.168.59.111 -p 9911). I have the default key to enable public key authentication. On the desktop server, I need a lightweight service that dynamically reads the newly fetched markdown format website, and ask LLM to assist my reading with system prompt to be specified by the user (could be translation task, problem-solving task, further study task, etc.). The LLM can be chosen by the user. The LLM needs to render the response in a reader-friendly HTML format, and the server needs to dynamically display the HTML content in a web page.

Please generate the chrome customized plguin in `chrome_plugin_module`.

Please generate the local client service module that stores webpage, transforms to markdown, and syncs up to the desktop server in `webpage_sync_module`.

Then, please generate the desktop server service module that reads the newly fetched markdown format website, and asks LLM to assist my reading with system prompt to be specified by the user (could be translation task, problem-solving task, further study task, etc.). The LLM can be chosen by the user. The LLM needs to render the response in a reader-friendly HTML format, and the server needs to dynamically display the HTML content in a web page in `desktop_server_module`.

## Recommended Tool Framework

For `chrome_plugin_module`, please use the standard chrome plugin development framework.

For all others, I would recommend you to develop based on Python. I am familiar with Python and AI (Torch/Numpy/Pandas) programming, and might be unfamiliar with other languages.

The `webpage_sync_module` is running on my local MacBook Pro.

The `aiserver_module` is running on my powerful desktop server with 4090 GPU and strong CPU.

## Recommended Guideline

- This is a cross-platform customized project.
- Being customized, we don't need to think about the generalizability and scalability of the code.
- Bring individual project, please follow good coding practices with documentation, so I can easily understand and maintain the code.
