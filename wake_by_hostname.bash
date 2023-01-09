#!/usr/bin/env bash

set -o pipefail

datafile="${XDG_DATA_HOME:-${HOME}/.local/share}/wake_by_hostname/macaddrs.txt"

declare -Ag host_to_mac

read_datafile () {
    if [ -r "$datafile" ]; then
        while read hostname mac_addr; do
            host_to_mac[$hostname]="$mac_addr"
        done <"$datafile"
    fi
}

read_mactable () {
    local hostname ip_addr mac_addr
    while read ip_addr _ mac_addr; do
       if [[ -n "$mac_addr" && -n "$ip_addr" ]]; then
           if hostname="$(ip_to_hostname "$ip_addr")"; then
               host_to_mac["$hostname"]="$mac_addr"
           fi
       fi
    done < <(ip -br neigh show nud reachable; ip -br neigh show nud stale)
}

print_mactable () {
    for hostname in "${!host_to_mac[@]}"; do
        printf "%s %s\n" "$hostname" "${host_to_mac[$hostname]}"
    done
}

ip_to_hostname () {
    host -W 1 -t ptr "$1" | sed 's/.* //; s/\.$//; s/\.lan$//'
}

update_datafile () {
    read_mactable
    mkdir -p "${datafile%/*}"
    print_mactable >"$datafile"
}

wake_host () {
    local hostname="$1" mac_addr
    if [[ -n "${host_to_mac[$hostname]}" ]]; then
        sudo ether-wake "${host_to_mac[$hostname]}"
    else
        echo "Mac address of $hostname not known" 2>&1
        exit 1
    fi
}

wait_for_host () {
    local tstart=$EPOCHSECONDS
    while (( EPOCHSECONDS < tstart + 30 )); do
        ping -c1 -w30 "$1" &>/dev/null && return
    done
    echo "Could not wake $1" 1>&2
    return 1
}

print_usage () {
    printf "%s\n" \
        "Usage:" \
        "   wake_by_hostname.bash <hostname...>" \
        "   wake_by_hostname.bash -u" \
        ""\
        "Args:" \
        "   -u   update database of mac addresses from current ARP table"
}

cleanup_children() {
    if [[ -n $(jobs) ]]; then
        env kill --timeout 1000 KILL --signal TERM $(jobs -p)
    fi
}

main () {
    trap cleanup_children EXIT
    if [[ $# == 0 ]]; then
        print_usage
    else
        read_datafile
        for arg in "$@"; do
            case "$arg" in
                "-u")
                    update_datafile
                    ;;
                "-h"|"--help")
                    print_usage
                    break
                    ;;
                *)
                    wake_host "$arg"
                    wait_for_host "$arg" &
                    ;;
            esac
        done
        # wait for all hosts to wake up or time out
        local failed=0
        while [[ -n "$(jobs)" ]]; do
            wait -fn || (( failed += 1 ))
        done
        return $(( failed > 0 ))
    fi
}

main "$@"
