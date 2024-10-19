const PublicKeyVerification = artifacts.require("PublicKeyVerification");

module.exports = function (deployer) {
  deployer.deploy(PublicKeyVerification);
};
