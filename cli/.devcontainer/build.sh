# Output repository name without owner
repositoryName=$(gh repo view --json name -q ".name")
repositoryNameWithOwner=$(gh repo view --json nameWithOwner -q ".nameWithOwner")
gitUserName=$(git config --global user.name)
gitUserEmail=$(git config --global user.email)
gpgAgentSocket=$(gpgconf --list-dirs agent-extra-socket)
sshAuthSock=$SSH_AUTH_SOCK
[ -z $sshAuthSock ] && sshAuthSock=$(gpgconf --list-dirs agent-ssh-socket)

# Are we in .devcontainer dir?
[ -f ./devcontainer.json ] && cd ..

postCreateEnvFile=.devcontainer/postCreate.env.tmp

[ -f $postCreateEnvFile ] && rm $postCreateEnvFile 
touch $postCreateEnvFile

echo repositoryName=$repositoryName >> $postCreateEnvFile
echo repositoryNameWithOwner=$repositoryNameWithOwner >> $postCreateEnvFile
echo gitUserName=\"$gitUserName\" >> $postCreateEnvFile
echo gitUserEmail=$gitUserEmail >> $postCreateEnvFile
echo sshAuthSock=$sshAuthSock >> $postCreateEnvFile
[ -z $gpgAgentSocket ] || echo gpgAgentSocket=$gpgAgentSocket >> $postCreateEnvFile
[ -z $sshAuthSock ] || echo sshAuthSock=$sshAuthSock >> $postCreateEnvFile

echo postCreateCommand env:
cat $postCreateEnvFile
echo

workspaceFolder=.

# Build with cache management
echo "Building DevContainer..."
devcontainer build --workspace-folder $workspaceFolder

# If build fails due to cache issues, rebuild without cache
if [ $? -ne 0 ]; then
    echo "Build failed, retrying without cache..."
    devcontainer build --workspace-folder $workspaceFolder --no-cache
fi

devcontainer up --workspace-folder $workspaceFolder --remove-existing-container