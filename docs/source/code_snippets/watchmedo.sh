watchmedo shell-command \
    --command 'bash runner.sh "${watch_event_type}" "${watch_src_path}"' \
    --recursive \
    .
