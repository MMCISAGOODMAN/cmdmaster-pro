def generate_bash_completion():
    return r"""# Bash completion for cmdmaster-pro
# Usage: eval "$(cmdmaster-pro --completion bash)"

_cmdmaster_pro() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="--history --clear-history --export-history --import-history --ai-config
          --interactive --explain --decode --copy --dry-run --yes --local-only --run
          --search --suggest --favorite --template --completion --version --help
          --json --no-color --no-cache --clear-cache --stdin
          --set-ai-url --set-ai-token --set-ai-model"

    case "${prev}" in
        --set-ai-url|--set-ai-token|--set-ai-model|--export-history|--import-history)
            return 0
            ;;
        --completion)
            COMPREPLY=( $(compgen -W "bash zsh" -- "${cur}") )
            return 0
            ;;
        --favorite)
            COMPREPLY=( $(compgen -W "list add remove" -- "${cur}") )
            return 0
            ;;
        --template)
            COMPREPLY=( $(compgen -W "list add remove" -- "${cur}") )
            return 0
            ;;
        --search|--suggest)
            return 0
            ;;
    esac

    if [[ "${cur}" == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    fi

    COMPREPLY=( $(compgen -f -- "${cur}") )
}

complete -F _cmdmaster_pro cmdmaster-pro
"""


def generate_zsh_completion():
    return r"""#compdef cmdmaster-pro
# Zsh completion for cmdmaster-pro
# Usage: eval "$(cmdmaster-pro --completion zsh)"

_cmdmaster_pro() {
    _arguments -C \
        '(--history)'{--history}'[View command history]' \
        '(--clear-history)'{--clear-history}'[Clear command history]' \
        '(--export-history)'{--export-history}'[Export history]:file:_files' \
        '(--import-history)'{--import-history}'[Import history]:file:_files' \
        '(--ai-config)'{--ai-config}'[View AI configuration]' \
        '(-i --interactive)'{-i,--interactive}'[Start interactive mode]' \
        '(-e --explain)'{-e,--explain}'[Show explanation]' \
        '(-d --decode)'{-d,--decode}'[Explain shell command]' \
        '(-c --copy)'{-c,--copy}'[Copy to clipboard]' \
        '(-n --dry-run)'{-n,--dry-run}'[Generate only]' \
        '(-y --yes)'{-y,--yes}'[Skip confirmation]' \
        '(-L --local-only)'{-L,--local-only}'[Use local engine only]' \
        '(-x --run)'{-x,--run}'[Execute generated command]' \
        '--json[Output JSON]' \
        '--no-color[Disable colors]' \
        '--no-cache[Skip cache]' \
        '--clear-cache[Clear cache]' \
        '--stdin[Read query from stdin]' \
        '--search[Search history]:query:' \
        '--suggest[Show suggestions]:prefix:' \
        '--favorite[Manage favorites]:action:(list add remove)' \
        '--template[Manage templates]:action:(list add remove)' \
        '--completion[Print completion script]:shell:(bash zsh)' \
        '--version[Show version]' \
        '--set-ai-url[Set AI URL]:url:' \
        '--set-ai-token[Set AI token]:token:' \
        '--set-ai-model[Set AI model]:model:' \
        '*:query:' && return 0
}

_cmdmaster_pro "$@"
"""
