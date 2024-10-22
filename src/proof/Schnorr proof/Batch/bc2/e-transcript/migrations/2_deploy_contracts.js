const SchnorrBatchVerification = artifacts.require("SchnorrBatchVerification");

module.exports = function (deployer) {
  deployer.deploy(SchnorrBatchVerification);
};
