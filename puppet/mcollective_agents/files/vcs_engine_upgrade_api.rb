module MCollective
  module Agent
    class Vcs_engine_upgrade_api<RPC::Agent
      action "hagrp_display_all_frozen" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_engine_upgrade_api.py"
      end
      action "haconf" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_engine_upgrade_api.py"
      end
      action "hagrp_freeze" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_engine_upgrade_api.py"
      end
      action "hagrp_unfreeze" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_engine_upgrade_api.py"
      end
      action "get_package_file_info" do
        implemented_by "/opt/mcollective/mcollective/agent/vcs_engine_upgrade_api.py"
      end
      action "file_exists" do
        exist
      end
      action "delete_file" do
        delete
      end

      def exist
          file = request[:file]
          reply[:out] = File.exist?(file)
          reply[:retcode] = 0
      end

      def delete
          file = request[:file]
          begin
              if File.exist?(file)
                  File.delete(file)
                  reply[:out] = "Deleted #{file}"
              end
              reply[:retcode] = 0
          rescue Exception => ex
              reply[:retcode] = 1
              reply[:err] = "Failed to delete #{file}: #{ex.message}"
          end
      end



    end
  end
end
