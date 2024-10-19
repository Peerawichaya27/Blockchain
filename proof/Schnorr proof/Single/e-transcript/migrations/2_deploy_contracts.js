const SchnorrVerification = artifacts.require("SchnorrVerification");

module.exports = function (deployer) {
  deployer.deploy(SchnorrVerification);
};
