set -eu

# Only run a flow when a new file is created.
if [ "$1" != "closed" ]; then
    exit
fi

FLOW_ID="your-flow-id-here"
FLOW_INPUT=$(cat << EOF
{
    "event": "$1",
    "filename": "$2"
}
EOF
)

globus-automate flow run \
    --label "File change: $1" \
    --flow-input "${FLOW_INPUT}" \
    "${FLOW_ID}"
