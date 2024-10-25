const SchnorrSingleVerification = artifacts.require("SchnorrSingleVerification");

module.exports = function (deployer) {
  deployer.deploy(SchnorrSingleVerification);
};
