module MCollective
  module Agent
    class Vcs_node_upgrade_ordering_api < RPC::Agent
      action "hagrp_state" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_node_upgrade_ordering_api.py"
      end
      action "hagrp_display_frozen" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_node_upgrade_ordering_api.py"
      end
      action "causal_cluster_overview" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_node_upgrade_ordering_api.py"
      end
    end
  end
end
