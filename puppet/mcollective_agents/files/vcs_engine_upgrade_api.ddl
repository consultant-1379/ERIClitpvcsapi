metadata    :name        => "vcs_engine_upgrade_api",
            :description => "API to access VCS upgrade",
            :author      => "Ericsson AB",
            :license     => "Ericsson",
            :version     => "1.0",
            :url         => "http://ericsson.com",
            :timeout     => 60

action "hagrp_display_all_frozen", :description => "access hagrp display frozen
command" do
    display :always

    output :retcode,
           :description => "The exit code from running the command",
           :display_as => "Result code"

    output :out,
           :description => "The stdout from running the command",
           :display_as => "out"

    output :err,
           :description => "The stderr from running the command",
           :display_as => "err"

end

action "haconf", :description => "access haconf command" do
    display :always

    input  :haaction,
           :prompt      => "action",
           :description => "makerw or makero",
           :type        => :list,
           :optional    => false,
           :list        => ["makerw", "makero"]

    output :retcode,
           :description => "The exit code from running the command",
           :display_as => "Result code"

    output :out,
           :description => "The stdout from running the command",
           :display_as => "out"

    output :err,
           :description => "The stderr from running the command",
           :display_as => "err"

end

action "hagrp_freeze", :description => "Freezes a group" do
    display :always

    input  :group_name,
           :prompt      => "Group Name",
           :description => "The name of the group",
           :type        => :string,
           :validation  => '',
           :optional    => false,
           :maxlength   => 0

    output :retcode,
           :description => "The exit code from running the command",
           :display_as => "Result code"

    output :out,
           :description => "The stdout from running the command",
           :display_as => "out"

    output :err,
           :description => "The stderr from running the command",
           :display_as => "err"

end

action "hagrp_unfreeze", :description => "Unfreeze a group" do
    display :always

    input  :group_name,
           :prompt      => "Group Name",
           :description => "The name of the group",
           :type        => :string,
           :validation  => '',
           :optional    => false,
           :maxlength   => 0

    output :retcode,
           :description => "The exit code from running the command",
           :display_as => "Result code"

    output :out,
           :description => "The stdout from running the command",
           :display_as => "out"

    output :err,
           :description => "The stderr from running the command",
           :display_as => "err"

end

action "get_package_file_info", :description => "get file info from an RPM" do
    display :always

    input   :package,
            :prompt      => "package",
            :description => "Package we want info from",
            :type        => :string,
            :validation  => '',
            :optional    => false,
            :maxlength   => 0

    output :retcode,
           :description => "The exit code from running the command",
           :display_as => "Result code"

    output :out,
           :description => "The stdout from running the command",
           :display_as => "out"

    output :err,
           :description => "The stderr from running the command",
           :display_as => "err"
end

action "file_exists", :description => "Check if file exists" do
    input   :file,
            :prompt      => "file",
            :description => "Path to a file",
            :type        => :string,
            :validation  => '^.+$',
            :optional    => false,
            :maxlength   => 256

    output :retcode,
           :description => "The exit code from running the command",
           :display_as => "Result code"

    output :out,
           :description => "Returns true if file exists, false if not",
           :display_as => "out"

    output :err,
           :description => "The stderr from running the command",
           :display_as => "err"
end

action "delete_file", :description => "Delete a files if it exists" do
    input   :file,
            :prompt      => "file",
            :description => "Path to a file",
            :type        => :string,
            :validation  => '^.+$',
            :optional    => false,
            :maxlength   => 256

    output :retcode,
           :description => "The exit code from running the command",
           :display_as => "Result code"

    output :out,
           :description => "Returns true if file exists, false if not",
           :display_as => "out"

    output :err,
           :description => "The stderr from running the command",
           :display_as => "err"
end
