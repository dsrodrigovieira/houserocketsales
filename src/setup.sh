mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"dsrodrigovieira@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCROS = false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml