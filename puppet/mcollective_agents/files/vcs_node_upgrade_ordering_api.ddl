metadata    :name        => "vcs_node_upgrade_ordering_api",
            :description => "API to access VCS cli command for node upgrade ordering",
            :author      => "Ericsson AB",
            :license     => "Ericsson",
            :version     => "1.0",
            :url         => "http://ericsson.com",
            :timeout     => 60

action "hagrp_state", :description => "access hagrp -state command" do
    display :always

    input  :group_name,
           :prompt      => "Group Name",
           :description => "The name of the group",
           :type        => :string,
           :validation  => '',
           :optional    => false,
           :maxlength   => 0

    input  :sys,
           :prompt      => "Node ID",
           :description => "The ID of the node",
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

action "hagrp_display_frozen", :description => "access hagrp frozen/tfrozen command" do
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

action "causal_cluster_overview", :description => "access neo4j cluster overview command" do
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
